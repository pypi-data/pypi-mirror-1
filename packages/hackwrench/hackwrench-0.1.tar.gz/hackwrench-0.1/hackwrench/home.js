window.onload=function(){
//document.write('<html><head><title>Speed Dial</title></head><body><div id="body"></div></body></html>');

window.speedDial = {
  'rows': 3,
  'cols': 3,
  'data': [''] 
}

var body = document.getElementById('body'); 

window.speedDial.rows = 3;
window.speedDial.cols = 3;

    var changeSite = function(id) {
      database.transaction(function(tx) {
        tx.executeSql('SELECT * FROM SpeedDialSites WHERE id = ?', [id], function(tx, result) {
          if (result.rows.length == 0) {
            var url = checkURL(window.prompt('Enter the URL for cell ' + id));
            
            if (url === false) {
              return;
            }

            if (url.length > 0) {
              tx.executeSql('INSERT INTO SpeedDialSites (id, url) VALUES (?, ?)', [id, url], function(tx, result) {
                window.setTimeout(function() {
                  render();
                }, 400);
              }, function(tx, error) {
                alert(error.message);
              });
            }

          } else if (result.rows.length == 1) {
            var row = result.rows.item(0);
            var url = checkURL(window.prompt('Enter the URL for cell ' + id, row.url));
            
            if (url === false) {
              return;
            }

            if (url.length > 0) {
              tx.executeSql('UPDATE SpeedDialSites SET id = ?, url = ?', [id, url], function(tx, result) {
                window.setTimeout(function() {
                  render();
                }, 400);
              }, function(tx, error) {
                alert(error.message);
              });

            } else {
              tx.executeSql('DELETE FROM SpeedDialSites WHERE id = ?', [id], function(tx, result) {
                window.setTimeout(function() {
                  render();
                }, 400);
              }, function(tx, error) {
                alert(error.message);
              });
            }

          } else {
            alert('Too many rows!');
            return;
          }
          
        }, function(tx, error) {
          alert('Error with SpeedDialSites table');
          return;
        });
      })
    }
    
    var clearAll = function() {
      database.transaction(function(tx) {
        tx.executeSql('DELETE FROM SpeedDialSites WHERE id > -1', [], function(tx, result) {
          // success
        }, function(tx, error) {
          alert(error.message);
        });
      });
      
      window.setTimeout(function() {
        render();
      }, 400);
      
      return true;
    }
    
    var changeSettings = function() {
      var rows = parseInt(prompt('Please enter the number of rows you require'));
      var cols = parseInt(prompt('Please enter the number of columns you require'));
      
      database.transaction(function(tx) {
        tx.executeSql('UPDATE SpeedDialSettings SET rows = ?, cols = ? WHERE rows = ? AND cols = ?', [rows,cols,window.speedDial.rows,window.speedDial.cols], function(tx, result) {
          // success
        }, function(tx, error) {
          alert(error.message);
        });
      });
      
      loadSettings();
      
      window.setTimeout(function() {
        render();
      }, 400);
    }
    
    var checkURL = function(url) {
      if (url == null) {
        return false;
      }

      if (typeof url != 'string') {
        return '';

      } else {
        if (url.length > 0) {
          if (url.indexOf('http') == -1) {
            return 'http://' + url;

          } else {
            return url;
          }

        } else {
          return '';
        }
      }
    }

    database.transaction(function(tx) {
      tx.executeSql('SELECT * FROM SpeedDialSettings', [], function(tx, result) {
        if (result.rows.length == 0) {
          tx.executeSql('INSERT INTO SpeedDialSettings (rows,cols) VALUES (?, ?)', [3, 3]);
          // working ok

        } else {
          // working ok
        }
      }, function(tx, error) {
        tx.executeSql('CREATE TABLE SpeedDialSettings (rows REAL, cols REAL)', [], function(tx, result) {
          tx.executeSql('INSERT INTO SpeedDialSettings (rows,cols) VALUES (?, ?)', [3, 3]);
        });
        // working ok too!
      });
    });

    database.transaction(function(tx) {
      tx.executeSql('SELECT COUNT(*) FROM SpeedDialSites', [], function(tx, result) {
        // working ok
      }, function(tx, error) {
        tx.executeSql('CREATE TABLE SpeedDialSites (id REAL UNIQUE, url TEXT)'), [], function(tx, result) {
          // now working ok too
        }
      });
    });
    
    var render = function() {
      
      body.innerHTML = '';

      var table = document.createElement('table');
      table.cellSpacing = '10px';
      table.style.width = '90%';
      table.style.height = '90%';
      table.style.marginTop = '5%';
      table.style.marginLeft = '5%';
      body.appendChild(table);

      for (var i = 1; i <= window.speedDial.rows; i++) {
        var row = document.createElement('tr');
        table.appendChild(row);

        for (var j = 1; j <= window.speedDial.cols; j++) {
          var num = (((i - 1) * window.speedDial.cols) + j);
          var cell = document.createElement('td');
          cell.style.color = '#ccc';
          cell.style.border = '8px solid #ccc';
          cell.style.textAlign = 'center';
          cell.style.fontFamily = 'Arial';
          cell.style.width = parseInt(100 / window.speedDial.cols) + '%';
          cell.style.height = parseInt(100 / window.speedDial.rows) + '%';
          cell.num = num;

          cell.onclick = function() {
            if (this.innerHTML == this.num || !this.url) {
              changeSite(this.num);

            } else {
              if (event.altKey) {
                changeSite(this.num);

              } else {
                window.location = this.url;
              }
            }
          }

          cell.onmouseover = function() {
            this.style.color = '#999';
            this.style.border = '8px solid #999';
          }

          cell.onmouseout = function() {
            this.style.color = '#ccc';
            this.style.border = '8px solid #ccc';
          }

          if (typeof window.speedDial.data[num] == 'undefined') {
            cell.style.color = '#ccc';
            cell.style.fontSize = '100px';
            cell.innerHTML = num;

          } else {
            cell.url = window.speedDial.data[num];
            cell.style.fontSize = '15px';
            cell.innerHTML = '<img src="http://snapcasa.com/get.aspx?code=SNAPCASA_CODE&size=l&url=' + cell.url + '" alt=""/>';
          }

          row.appendChild(cell);
        }
      }
      
      var link = document.createElement('a');
      link.href = '#';

      link.onclick = function() {
        clearAll();
        return false;
      }

      link.appendChild(document.createTextNode('Clear'));
      
      var link2 = document.createElement('a');
      link2.href = '#';

      link2.onclick = function() {
        changeSettings();
        return false;
      }

      link2.appendChild(document.createTextNode('Settings'));
      
      link.style.color = '#ccc';
      link.style.textDecoration = 'none';
      link2.style.color = '#ccc';
      link2.style.textDecoration = 'none';
      
      var para = document.createElement('p');
      para.style.fontFamily = 'Arial';
      para.style.color = '#ccc';
      
      para.appendChild(link)
      para.appendChild(document.createTextNode(' - '))
      para.appendChild(link2)
      body.appendChild(para);
    }

    loadSettings();
    loadData();
    
    window.setTimeout(function() { render(); }, 100);
  //} else {
  //  body.innerHTML = 'Error opening database';
  }

} else {
  body.innerHTML = 'Error accessing database'; 
}
}
